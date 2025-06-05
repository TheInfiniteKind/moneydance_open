/**
 * Copyright 2018 Mike Bray (mrbtrash2@btinternet.com)
 * 
 * Based on work by hleofxquotes@gmail.com 
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.moneydance.modules.features.reportwriter;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.io.InputStream;
import java.sql.Date;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.jar.JarFile;

import com.infinitekind.moneydance.model.AbstractTxn;
import com.moneydance.modules.features.mrbutil.MRBDebug;
import com.moneydance.modules.features.mrbutil.MRBDirectoryUtils;
import com.moneydance.util.Platform;

public abstract class Utilities {
   public static final File getLauncherFile() {
        File direct = MRBDirectoryUtils.getExtensionDataDirectory(Constants.PROGRAMNAME);
        List<File> dirs = new ArrayList<>();
        dirs.add(direct);
        FileFilter filter = new FileFilter() {

            @Override
            public boolean accept(File pathname) {
                if (!pathname.isFile()) {
                    return false;
                }

                String name = pathname.getName();
                if (!name.startsWith("MD")) {
                	return false;
                }
                if (!name.endsWith(".jar")) {
                    return false;
                }

                boolean rv = false;
                try {
                    try (JarFile jarFile = new JarFile(pathname)) {
                        rv = true;
                   }
                } catch (IOException e) {
                	Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.DETAILED, e.getMessage());
                }

                return rv;
            }
        };

        List<File> jarFiles = new ArrayList<>();
        for (File dir : dirs) {
        	Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"WRITER - looking for exec jar file in dir=" + dir.getAbsolutePath());
            File[] files = dir.listFiles(filter);
            jarFiles.addAll(Arrays.asList(files));
        }

        Comparator<File> comparator = new Comparator<File>() {
            @Override
            public int compare(File f1, File f2) {
                int rv = 0;
                 int b1 = getBuildNumber(f1);
                int b2 = getBuildNumber(f2);
                Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"WRITER - f1=" + f1.getName() + ", b1=" + b1);
                Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"WRITER - f2=" + f2.getName() + ", b2=" + b2);
                if ((b1 > 0) && (b2 > 0)) {
                    rv = b1 - b2;
                    rv = -rv;
                } else {
                    long m1 = f1.lastModified();
                    long m2 = f2.lastModified();
                    Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"WRITER - f1=" + f1.getName() + ", m1=" + m1);
                    Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"WRITER - f2=" + f2.getName() + ", m2=" + m2);
                    rv = (int) (m1 - m2);
                    rv = -rv;
                }

                Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"WRITER- compare exec f1=" + f1.getName() + ", f2=" + f2.getName() + ", rv=" + rv);

                return rv;
            }

            private int getBuildNumber(File file) {
                int buildNumber = 0;
                String name = file.getName();
                String[] tokens = name.split("-");
                if (tokens.length == 4) {
                    String buildString = tokens[2];
                    tokens = buildString.split("_");
                    if (tokens.length == 3) {
                        try {
                            buildString = tokens[2];
                            buildNumber = Integer.valueOf(buildString);
                        } catch (NumberFormatException e) {
                        	Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,e.getMessage());
                            buildNumber = 0;
                        }
                    }
                }
                return buildNumber;
            }
        };
        Collections.sort(jarFiles, comparator);

        Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"MDJasperServer- found " + jarFiles.size() + " exec jar file(s) ...");
        for (File jarFile : jarFiles) {
        	Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"MDJasperServer - exec jarFile=" + jarFile.getAbsolutePath());
        }
        File jarFile = null;
        if (jarFiles.size() > 0) {
            jarFile = jarFiles.get(0);
            Main.rwDebugInst.debug("Utilities","getLauncherFile",MRBDebug.SUMMARY,"MDJasperServer- Jasper exec jar file=" + jarFile.getAbsolutePath());
        }
        return jarFile;
    }
    public static final File getDatabaseFile() {
        File direct = MRBDirectoryUtils.getExtensionDataDirectory(Constants.PROGRAMNAME);
        List<File> dirs = new ArrayList<>();
        dirs.add(direct);
        FileFilter filter = new FileFilter() {

            @Override
            public boolean accept(File pathname) {
                if (!pathname.isFile()) {
                    return false;
                }

                String name = pathname.getName();
                if (!name.startsWith("h2-") || !name.endsWith(".jar")) {
                    return false;
                }

                boolean rv = false;
                try {
                    try (JarFile jarFile = new JarFile(pathname)) {
                        rv = true;
                   }
                } catch (IOException e) {
                	Main.rwDebugInst.debug("Utilities","getDatabaseFile",MRBDebug.DETAILED, e.getMessage());
                }

                return rv;
            }
        };

        List<File> jarFiles = new ArrayList<>();
        for (File dir : dirs) {
        	Main.rwDebugInst.debug("Utilities","getDatabaseFile",MRBDebug.SUMMARY,"WRITER - looking for exec jar file in dir=" + dir.getAbsolutePath());
            File[] files = dir.listFiles(filter);
            jarFiles.addAll(Arrays.asList(files));
        }

 

        Main.rwDebugInst.debug("Utilities","getDatabaseFile",MRBDebug.SUMMARY,"h2 file found- found " + jarFiles.size() + " exec jar file(s) ...");
        for (File jarFile : jarFiles) {
        	Main.rwDebugInst.debug("Utilities","getDatabaseFile",MRBDebug.SUMMARY,"h2 file  - exec jarFile=" + jarFile.getAbsolutePath());
        }
        File jarFile = null;
        if (jarFiles.size() <= 0) {
        	Main.rwDebugInst.debug("Utilities","getDatabaseFile",MRBDebug.SUMMARY, "Cannot find the database jar file.");
        } else {
            jarFile = jarFiles.get(0);
            Main.rwDebugInst.debug("Utilities","getDatabaseFile",MRBDebug.SUMMARY,"h2 file - Database exec jar file=" + jarFile.getAbsolutePath());
        }

        return jarFile;
    }
    public static String getDateStr(Integer date) {
    	String dateStr;
    	if (date == null)
    		return "1971-01-01";
    	dateStr = String.valueOf(date/10000);
    	dateStr += "-"+String.valueOf((date - (date/10000)*10000)/100);
    	dateStr += "-" + String.valueOf(date - (date/100)*100);
    	return dateStr;
    }
	public static Date getSQLDate(Integer date) {
		Date sqlDate=null;
		try {
			sqlDate = Date.valueOf(getDateStr(date));
		}
		catch (Exception e) {
			sqlDate = new Date(0L);
		}
		return sqlDate;
	}
	public static void notifyUser(String message) {
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
			@Override
			public void run() {
				Main.context.showURL("moneydance:setprogress?meter=0&label="+
				         message);
				Main.rwDebugInst.debug("Utilities", "notifyUser", MRBDebug.DETAILED, message);

			}
		});

	}
	public static String getTxnStatus(byte status) {
		switch (status) {
		case AbstractTxn.STATUS_CLEARED:
			return "Cleared";
		case AbstractTxn.STATUS_RECONCILING:
			return "Reconciling";
		case AbstractTxn.STATUS_UNRECONCILED:
			return "Unreconciled";
		}
		return "Unknown";
	}
	public class CustomClassLoader extends ClassLoader {
		 
	    @Override
	    public Class<?> findClass(String name) throws ClassNotFoundException {
	        byte[] b = loadClassFromFile(name);
	        return defineClass(name, b, 0, b.length);
	    }
	 
	    private byte[] loadClassFromFile(String fileName)  {
	        InputStream inputStream = getClass().getClassLoader().getResourceAsStream(
	                fileName.replace('.', File.separatorChar) + ".class");
	        byte[] buffer;
	        ByteArrayOutputStream byteStream = new ByteArrayOutputStream();
	        int nextValue = 0;
	        try {
	            while ( (nextValue = inputStream.read()) != -1 ) {
	                byteStream.write(nextValue);
	            }
	        } catch (IOException e) {
	            e.printStackTrace();
	        }
	        buffer = byteStream.toByteArray();
	        return buffer;
	    }
	}
   }

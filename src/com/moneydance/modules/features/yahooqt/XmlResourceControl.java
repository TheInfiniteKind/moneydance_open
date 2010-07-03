package com.moneydance.modules.features.yahooqt;

import java.util.ResourceBundle;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Locale;
import java.util.Properties;
import java.util.Enumeration;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;
import java.security.AccessController;
import java.security.PrivilegedExceptionAction;
import java.security.PrivilegedActionException;

/**
 * A {@link ResourceBundle.Control} subclass that allows loading of bundles in XML format.
 * <p/>
 * The bundles are searched first as Java classes, then as properties files (these two methods are
 * the standard search mechanism of ResourceBundle), then as XML properties files.
 * <p/>
 * The filename extension of the XML properties files is assumed to be <code>*.properties.xml</code>
 *
 * <p>This code is adapted from code presented in the Sun Javadocs for
 * {@link ResourceBundle.Control} and other places.</p>
 * 
 * <p>This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />

 * @author Kevin Menningen
 * @version 1.0
 * @since 1.0
 */
class XmlResourceControl extends ResourceBundle.Control
{
    private static final List<String> FORMATS;

    static
    {
        List<String> formats = new ArrayList<String>(FORMAT_DEFAULT);
        formats.add(N12EStockQuotes.FORMAT_XML);
        FORMATS = Collections.unmodifiableList(formats);
    }

    @Override
    public List<String> getFormats(String baseName)
    {
        return FORMATS;
    }

    @Override
    public ResourceBundle newBundle(String baseName, Locale locale,
                                    String format, ClassLoader loader,
                                    boolean reload)
            throws IllegalAccessException, InstantiationException, IOException
    {
        if (baseName == null || format == null || loader == null)
        {
            throw new NullPointerException();
        }
        if (!N12EStockQuotes.FORMAT_XML.equals(format))
        {
            return super.newBundle(baseName, locale, format, loader, reload);
        }

        String bundleName = toBundleName(baseName, locale);
        String resourceName = toResourceName(bundleName, N12EStockQuotes.FORMAT_XML_SUFFIX);
        InputStream stream = getResourceInputStream(loader, resourceName, reload);
        if (stream == null)
        {
            // not found -- there is no XML implementation for the given locale
            return null;
        }

        try
        {
            PropertyXMLResourceBundle result = new PropertyXMLResourceBundle();
            result.load(stream);
            return result;
        }
        catch (IOException ioex)
        {
            final PrintStream output = System.err;
            output.println(N12EStockQuotes.XML_RESOURCE_LOAD_FAIL + resourceName);
            ioex.printStackTrace(output);
        }
        finally
        {
            stream.close();
        }

        return null;
    }

    /**
     * Get an input stream on the resource file.
     * <p/>
     * The original code used URLs and {@link java.net.URL#openConnection()} or
     * {@link java.net.URL#openStream()}. However, in some circumstances the resource URL couldn't
     * be found even though getResourceAsStream() could find it. Therefore this approach of using
     * getResourceAsStream() appears to work in more circumstances and is therefore more reliable.
     * @param loader       Class loader from which to retrieve the resource file.
     * @param resourceName The fully qualified name (already resolved) of the resource.
     * @param reload       True if forcing a complete reload.
     * @return The input stream of the resource XML file.
     * @throws IOException If a problem occurs locating or opening the resource file.
     */
    private InputStream getResourceInputStream(final ClassLoader loader, final String resourceName,
                                               boolean reload)
            throws IOException
    {
        if (!reload)
        {
            return loader.getResourceAsStream(resourceName);
        }

        try
        {
            return AccessController.doPrivileged(
                    new PrivilegedExceptionAction<InputStream>()
                    {
                        public InputStream run() throws IOException
                        {
                            return loader.getResourceAsStream(resourceName);
                        }
                    });
        }
        catch (PrivilegedActionException privEx)
        {
            throw (IOException) privEx.getCause();
        }
    }

    /**
     * ResourceBundle that loads definitions from an XML properties file.
     */
    public static class PropertyXMLResourceBundle extends ResourceBundle
    {
        private final Properties _properties = new Properties();

        public void load(InputStream stream) throws IOException
        {
            _properties.loadFromXML(stream);
        }

        protected Object handleGetObject(String key)
        {
            return _properties.getProperty(key);
        }

        public Enumeration<String> getKeys()
        {
            final Enumeration<Object> keys = _properties.keys();
            return new Enumeration<String>()
            {
                public boolean hasMoreElements()
                {
                    return keys.hasMoreElements();
                }

                public String nextElement()
                {
                    return (String) keys.nextElement();
                }
            };
        }
    }
}
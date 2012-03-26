/*
 * ************************************************************************
 * Copyright (C) 2012 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import java.util.ResourceBundle;
import java.util.Enumeration;
import java.util.Properties;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.Iterator;
import java.io.InputStream;
import java.io.IOException;

/**
 * Resource bundle that is capable of reading the resources from an XML file.
 *
 * @author Kevin Menningen
 */
class XmlResourceBundle extends ResourceBundle {
  /**
   * The map to lookup a string from a key.
   */
  private final Map<String, Object> _lookup;

  /**
   * Creates a property resource bundle with no parent.
   *
   * @param stream property file to read from.
   * @throws IOException If an error occurs loading the table.
   */
  public XmlResourceBundle(InputStream stream) throws IOException {
    this(stream, null);
  }

  /**
   * Creates a property resource bundle with an optional parent.
   *
   * @param stream property file to read from.
   * @param parent The parent resource bundle for this one.
   * @throws IOException If an error occurs loading the table.
   */
  public XmlResourceBundle(InputStream stream, ResourceBundle parent) throws IOException {
    // first load any localized resources for the current language
    Properties properties = new Properties();
    properties.loadFromXML(stream);
    _lookup = new HashMap<String, Object>();
    Enumeration keyEnum = properties.propertyNames();
    while (keyEnum.hasMoreElements()) {
      String key = (String) keyEnum.nextElement();
      _lookup.put(key, properties.getProperty(key));
    }
    // then fill in any gaps from the (optional) parent bundle
    if (parent != null) setParent(parent);
  }

  // Implements java.util.ResourceBundle.handleGetObject; inherits javadoc specification.

  public Object handleGetObject(String key) {
    if (key == null) {
      throw new NullPointerException();
    }
    return _lookup.get(key);
  }

  @Override
  protected void setParent(ResourceBundle parent) {
    Enumeration<String> parentKeys = parent.getKeys();
    while (parentKeys.hasMoreElements()) {
      // fill in the parent (English) values if the child doesn't have them
      String key = parentKeys.nextElement();
      if (!_lookup.containsKey(key)) {
        _lookup.put(key, parent.getObject(key));
      }
    }
  }

  /**
   * Implementation of ResourceBundle.getKeys.
   */
  public Enumeration<String> getKeys() {
    return new StringEnumerator(_lookup.keySet());
  }

  private class StringEnumerator implements Enumeration<String> {
    private final Iterator<String> _iterator;

    StringEnumerator(final Set<String> keys) {
      _iterator = keys.iterator();
    }

    public boolean hasMoreElements() {
      return _iterator.hasNext();
    }

    public String nextElement() {
      return _iterator.next();
    }
  }
}

/*************************************************************************\
 * Copyright (C) 2010 The Infinite Kind, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
\*************************************************************************/
package com.moneydance.modules.features.yahooqt

import java.io.InputStream
import java.util.*

/**
 * Resource bundle that is capable of reading the resources from an XML file.
 *
 * @author Kevin Menningen
 */
internal class XmlResourceBundle @JvmOverloads constructor(stream: InputStream?, parent: ResourceBundle? = null) : ResourceBundle() {
  /**
   * The map to lookup a string from a key.
   */
  private val _lookup: MutableMap<String, Any>
  
  /**
   * Creates a property resource bundle with an optional parent.
   *
   * @param stream property file to read from.
   * @param parent The parent resource bundle for this one.
   * @throws IOException If an error occurs loading the table.
   */
  /**
   * Creates a property resource bundle with no parent.
   *
   * @param stream property file to read from.
   * @throws IOException If an error occurs loading the table.
   */
  init {
    // first load any localized resources for the current language
    val properties = Properties()
    properties.loadFromXML(stream)
    _lookup = HashMap()
    val keyEnum = properties.propertyNames()
    while (keyEnum.hasMoreElements()) {
      val key = keyEnum.nextElement() as String
      _lookup[key] = properties.getProperty(key)
    }
    // then fill in any gaps from the (optional) parent bundle
    if (parent != null) setParent(parent)
  }
  
  // Implements java.util.ResourceBundle.handleGetObject; inherits javadoc specification.
  public override fun handleGetObject(key: String): Any {
    if (key == null) {
      throw NullPointerException()
    }
    return _lookup[key]!!
  }
  
  override fun setParent(parent: ResourceBundle) {
    val parentKeys = parent.keys
    while (parentKeys.hasMoreElements()) {
      // fill in the parent (English) values if the child doesn't have them
      val key = parentKeys.nextElement()
      if (!_lookup.containsKey(key)) {
        _lookup[key] = parent.getObject(key)
      }
    }
  }
  
  /**
   * Implementation of ResourceBundle.getKeys.
   */
  override fun getKeys(): Enumeration<String> {
    return StringEnumerator(_lookup.keys)
  }
  
  private inner class StringEnumerator(keys: Set<String>) : Enumeration<String> {
    private val _iterator = keys.iterator()
    
    override fun hasMoreElements(): Boolean {
      return _iterator.hasNext()
    }
    
    override fun nextElement(): String {
      return _iterator.next()
    }
  }
}

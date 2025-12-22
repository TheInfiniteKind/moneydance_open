/*
 * Copyright (c) 2009-2025 The Infinite Kind, Limited
 */
package com.moneydance.modules.features.yahooqt

import com.infinitekind.moneydance.model.CurrencyListener
import com.infinitekind.moneydance.model.CurrencySearch
import com.infinitekind.moneydance.model.CurrencyTable
import com.infinitekind.moneydance.model.CurrencyType
import javax.swing.AbstractListModel
import javax.swing.ComboBoxModel
import java.util.Collections
import java.util.Locale

val CURRENCY_TYPENAME_CASE_INSENSITIVE_COMPARATOR = Comparator<CurrencyType> { currencyType, currencyType2 ->
  val typeCmp = currencyType.currencyType.compareTo(currencyType2.currencyType)
  if (typeCmp != 0) typeCmp else currencyType.getName().lowercase(Locale.getDefault()).compareTo(currencyType2.getName().lowercase(Locale.getDefault()))
}



/**
 * Model used to represent a set of currency values.
 */
class CustomCurrencyModel(
  private val currencyTable: CurrencyTable,
  private var filter: CurrencySearch? = null,
  private var currencyType: CurrencyType.Type? = null
) : AbstractListModel<CurrencyType>(), ComboBoxModel<CurrencyType>, CurrencyListener {
  
  private val currencies: MutableList<CurrencyType> = ArrayList()
  private var selectedType: CurrencyType? = null
  
  init {
    resynchronize()
    if (currencies.isNotEmpty()) {
      selectedType = currencyTable.baseType.takeIf { currencies.contains(it) } ?: currencies[0]
    }
    currencyTable.addCurrencyListener(this)
  }
  
  /**
   * Convenience secondary constructor to match original Java overload:
   * CustomCurrencyModel(currencyTable, filter)
   */
  constructor(currencyTable: CurrencyTable, filter: CurrencySearch?) : this(currencyTable, filter, null)
  
  /**
   * Convenience secondary constructor to match original Java overload:
   * CustomCurrencyModel(currencyTable, currencyType)
   */
  constructor(currencyTable: CurrencyTable, currencyType: CurrencyType.Type?) : this(currencyTable, null, currencyType)
  
  fun goneAway() { currencyTable.removeCurrencyListener(this) }
  
  fun isVisible(c: CurrencyType?): Boolean {
    c ?: return false
    filter?.let { return it.matches(c) }
    currencyType?.let { return c.currencyType == it }
    return true
  }
  
  @Synchronized
  fun resynchronize() {
    currencies.clear()
    for (curr in currencyTable.allCurrencies) {
      if (isVisible(curr)) currencies.add(curr)
    }
    // Use Collections.sort with the Java comparator to avoid adapter issues
    Collections.sort(currencies, CURRENCY_TYPENAME_CASE_INSENSITIVE_COMPARATOR)
    fireContentsChanged(this, -1, -1)
  }
  
  override fun currencyTableModified(table: CurrencyTable?) { resynchronize() }
  
  override fun getSize(): Int = currencies.size
  
  override fun getElementAt(i: Int): CurrencyType = currencies[i]
  
  override fun getSelectedItem(): Any? = selectedType
  
  /**
   * Set selected by index (safe).
   */
  fun setSelectedIndex(index: Int) { if (index in currencies.indices) setSelectedItem(currencies[index]) else setSelectedItem(null) }
  
  override fun setSelectedItem(item: Any?) {
    selectedType = item as? CurrencyType
    fireContentsChanged(this, -1, -1)
  }
}

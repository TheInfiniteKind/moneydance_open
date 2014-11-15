/*
 * ************************************************************************
 * Copyright (C) 2012-2013 Mennē Software Solutions, LLC
 *
 * This code is released as open source under the Apache 2.0 License:<br/>
 * <a href="http://www.apache.org/licenses/LICENSE-2.0">
 * http://www.apache.org/licenses/LICENSE-2.0</a><br />
 * ************************************************************************
 */

package com.moneydance.modules.features.ratios;

import com.infinitekind.moneydance.model.Account;
import com.infinitekind.moneydance.model.Txn;
import com.moneydance.apps.md.view.gui.MoneydanceGUI;
import com.infinitekind.util.StringUtils;

import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JViewport;
import java.awt.Component;
import java.awt.Container;
import java.awt.Desktop;
import java.awt.event.FocusListener;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Comparator;

/**
 * Utility methods.
 *
 * @author Kevin Menningen
 */
public final class RatiosUtil {

  /**
   * Compare two accounts by name, for sorting a list by account name. Uses the full name so that
   * sub-accounts are kept with their parent accounts.
   */
  private static final Comparator<Account> ACCOUNT_NAME_COMPARATOR = new Comparator<Account>() {
    public int compare(Account lhs, Account rhs) {
      if (lhs == null) { return (rhs == null) ? 0 : -1; }
      if (rhs == null) return 1;
      return lhs.getFullAccountName().compareTo(rhs.getFullAccountName());
    }
  };

  /**
   * Compare two accounts by type, for sorting a list by account type. This puts accounts in exactly the same
   * order as they appear in the side bar or in the account selector.
   */
  private static final Comparator<Account> ACCOUNT_TYPE_COMPARATOR = new Comparator<Account>() {
    public int compare(Account lhs, Account rhs) {
      if (lhs == null) { return (rhs == null) ? 0 : -1; }
      if (rhs == null) return 1;
      final int lType = lhs.getAccountType();
      final int rType = rhs.getAccountType();
      if (lType == rType) return 0; // shortcut
      // first put the non-income, non-expense accounts in account type order
      if ((lType != Account.ACCOUNT_TYPE_INCOME)
          && (lType != Account.ACCOUNT_TYPE_EXPENSE)
          && (rType != Account.ACCOUNT_TYPE_INCOME)
          && (rType != Account.ACCOUNT_TYPE_EXPENSE)) {
        return lType - rType;
      }
      // at this point one or both sides is a category
      if ((lType != Account.ACCOUNT_TYPE_INCOME) && (lType != Account.ACCOUNT_TYPE_EXPENSE)) {
        // normal accounts first, left hand side is normal account but right hand side isn't
        return -1;
      }
      if ((rType != Account.ACCOUNT_TYPE_INCOME) && (rType != Account.ACCOUNT_TYPE_EXPENSE)) {
        // normal accounts first, right hand side is normal account but left hand side isn't
        return 1;
      }
      // both are income or expense accounts, put income accounts first which is in reverse numerical order
      return rType - lType;
    }
  };

  private static final Comparator<Txn> TXN_ACCOUNT_COMPARATOR = new Comparator<Txn>() {
    public int compare(Txn lhs, Txn rhs) {
      final int result = ACCOUNT_TYPE_COMPARATOR.compare(lhs.getAccount(), rhs.getAccount());
      if (result != 0) return result;
      return ACCOUNT_NAME_COMPARATOR.compare(lhs.getAccount(), rhs.getAccount());
    }
  };
  
  private static final Comparator<Txn> TXN_DATE_COMPARATOR = new Comparator<Txn>() {
    public int compare(Txn lhs, Txn rhs) {
      return lhs.getDateInt() - rhs.getDateInt();
    }
  };
  
  private static final Comparator<Txn> TXN_TAX_DATE_COMPARATOR = new Comparator<Txn>() {
    public int compare(Txn lhs, Txn rhs) {
      return lhs.getTaxDateInt() - rhs.getTaxDateInt();
    }
  };
  
  private static final Comparator<Txn> TXN_AMOUNT_COMPARATOR = new Comparator<Txn>() {
    public int compare(Txn lhs, Txn rhs) {
      return (int)(rhs.getValue() - lhs.getValue());
    }
  };
  
  private static final Comparator<Txn> TXN_DATE_ENTERED_COMPARATOR = new Comparator<Txn>() {
    public int compare(Txn lhs, Txn rhs) {
      long dt1 = lhs.getDateEntered();
      long dt2 = rhs.getDateEntered();
      if(dt1<dt2) return -1;
      if(dt1>dt2) return 1;
      return 0;
    }
  };

  private static final Comparator<Txn> TXN_ID_COMPARATOR = new Comparator<Txn>() {
    public int compare(Txn lhs, Txn rhs) {
      int val = (int) (lhs.getTxnId() - rhs.getTxnId()); // last resort, compare the txn ID
      if (val != 0) return val;
      if (lhs == rhs) {
        return 0;
      } else {
        val = lhs.hashCode() - rhs.hashCode();
        if (val == 0) return -1;
        return val;
      }
    }
  };

  static Comparator<Account> getAccountComparator() {
    return createComparator(ACCOUNT_TYPE_COMPARATOR, ACCOUNT_NAME_COMPARATOR);
  }

  static Comparator<Txn> getTransactionComparator(final boolean useTaxDate) {
    return useTaxDate ?
           createComparator(TXN_ACCOUNT_COMPARATOR,
                            TXN_TAX_DATE_COMPARATOR,
                            TXN_AMOUNT_COMPARATOR,
                            TXN_DATE_ENTERED_COMPARATOR,
                            TXN_ID_COMPARATOR) :
           createComparator(TXN_ACCOUNT_COMPARATOR,
                            TXN_DATE_COMPARATOR,
                            TXN_AMOUNT_COMPARATOR,
                            TXN_DATE_ENTERED_COMPARATOR,
                            TXN_ID_COMPARATOR);
  }

  /**
   * Formats the given double [0..1.00] as a percentage with either zero (if an even percentage)
   * or two decimal digits showing. If <code>forceDecimal</code> is true, digits after the decimal
   * point will be displayed regardless of whether it is an even percentage or not.
   *
   * @param value         The value as a decimal (is multiplied by 100 for display).
   * @param decimalChar   The decimal character to display.
   * @param decimalPlaces How many digits past the decimal to display.
   * @return A percentage for display to the user, which will have 2 decimal digits unless it is
   * an even integer percent, in which case it will have no decimal digits displayed.
   */
  private static String formatPercent(double value, char decimalChar, int decimalPlaces) {
    String sValue = StringUtils.formatRate(value * 100.0, decimalChar);
    return StringUtils.formatFixedDecimals(sValue, decimalChar, decimalPlaces) + '%';
  }

  static String formatRatioValue(double value, char decimalChar, int decimalPlaces, String nanString, boolean showPercent) {
    if (Double.isInfinite(value) || Double.isNaN(value)) return nanString;
    if (showPercent) {
      if (decimalPlaces == 0) return StringUtils.formatPercentage(roundToDecimal(value, decimalPlaces + 2), decimalChar);
      return formatPercent(roundToDecimal(value, decimalPlaces + 2), decimalChar, decimalPlaces);
    }
    // show the number rounded to the correct number of digits
    if (decimalPlaces == 0) {
      // lop off the decimal char and any digits past it
      String sValue = StringUtils.formatRate(value, decimalChar);
      final int decimalIndex = sValue.indexOf(decimalChar);
      if (decimalIndex > 0) return sValue.substring(0, decimalIndex);
      return sValue;
    }
    String sValue = StringUtils.formatRate(roundToDecimal(value, decimalPlaces), decimalChar);
    return StringUtils.formatFixedDecimals(sValue, decimalChar, decimalPlaces);
  }

  public static double getConstantValue(String text, char decimal, boolean allowZero, double defaultValue) {
    double value = StringUtils.parseRate(text, Double.MAX_VALUE, decimal);
    boolean isError = isConstantError(allowZero, value);
    return isError ? defaultValue : value;
  }

  public static boolean getConstantError(String text, char decimal, boolean allowZero) {
    double value = StringUtils.parseRate(text, Double.MAX_VALUE, decimal);
    return isConstantError(allowZero, value);
  }

  private static boolean isConstantError(boolean allowZero, double value) {
    boolean isError = !allowZero && (value == 0.0);
    isError |= (value == Double.MAX_VALUE) || Double.isInfinite(value) || Double.isNaN(value);
    return isError;
  }

  private static double roundToDecimal(final double value, final int decimalPlaces) {
    final double power = Math.pow(10.0, (decimalPlaces < 1) ? 0 : decimalPlaces);
    return Math.round(value * power) / power;
  }

  public static String getAccountTypeNameAllCaps(final MoneydanceGUI mdGUI, final int accountType) {
    return mdGUI.getStr("acct_type"+accountType+'S');
  }
  /**
   * Get a label from (plugin) resources, and if it does not have a colon, add it. Also adds a
   * space at the end for better spacing in the UI layout.
   *
   * @param resources Resource provider.
   * @param key       String key to look up in the resources
   * @return A string with a colon at the end.
   */
  public static String getLabelText(final ResourceProvider resources, final String key) {
    return addLabelSuffix(resources, resources.getString(key));
  }

  /**
   * Determine if the matching logic is a balance logic or transaction-based logic. Transaction based logic scans each transaction and
   * can screen out transactions based on date and tags, but balance based computes the account balance, it includes all transactions.
   * @param logic The matching logic to check.
   * @return True if the logic is a balance-based type, or false if it is transaction-based.
   */
  public static boolean isAccountBalanceType(final TxnMatchLogic logic) {
    return TxnMatchLogic.END_BALANCE.equals(logic) || TxnMatchLogic.AVERAGE_BALANCE.equals(logic) || TxnMatchLogic.BEGIN_BALANCE.equals(logic);
  }

  /**
   * Add a colon prompt after a text label if it does not have a colon. Also adds a space at
   * the end for better spacing in the UI layout.
   *
   * @param resources Resource provider.
   * @param label     String to add the colon to.
   * @return A string with a colon at the end.
   */
  private static String addLabelSuffix(final ResourceProvider resources, final String label) {
    final StringBuilder result = new StringBuilder(label);
    if ((result.length() > 0) && (result.charAt(result.length() - 1)) != ':') {
      result.append(resources.getString(L10NRatios.LABEL_COLON));
    }
    result.append(' ');
    return result.toString();
  }

  static void recurseAddFocusListener(final Container root, final FocusListener listener) {
    for (Component child : root.getComponents()) {
      if ((child instanceof JPanel)
          || (child instanceof JScrollPane)
          || (child instanceof JViewport)) {
        recurseAddFocusListener((Container) child, listener);
      }
      if (child.isFocusable()) {
        // setup a focus traversal policy
        child.addFocusListener(listener);
      }
    }
  }
  
  private static <T> Comparator<T> createComparator(final Comparator<T>... comparators) {
    return new Comparator<T>() {
      public int compare(final T lhs, final T rhs) {
        int result = 0;
        for (Comparator<T> comp : comparators) {
          result = comp.compare(lhs, rhs);
          if (result != 0) break;
        }
        return result;
      }
    };
  }

  /**
   * Determine if two objects of the same type are equal or not.
   * @param object1 Left hand side object.
   * @param object2 Right hand side object.
   * @param <T> The type of object being compared.
   * @return True if the objects are equal, false otherwise.
   */
  public static <T> boolean areEqual(final T object1, final T object2) {
    if (object1 == object2) return true;                      // either same instance or both null
    if ((object1 == null) || (object2 == null)) return false; // one is null, the other isn't
    return object1.equals(object2);
  }

  public static void launchUserGuide() {
    if (Desktop.isDesktopSupported()) {
      try {
        Desktop.getDesktop().browse(new URI("http://www.mennesoft.com/ratios/index.html#usage"));
      } catch (IOException e) {
        System.err.println("ratios: Unable to launch browser for user guide - IO exception");
      } catch (URISyntaxException e) {
        System.err.println("ratios: Unable to launch browser for user guide - URL issue");
      }
    }
  }

  /**
   * Static utilities only - do not instantiate.
   */
  private RatiosUtil() { }
}

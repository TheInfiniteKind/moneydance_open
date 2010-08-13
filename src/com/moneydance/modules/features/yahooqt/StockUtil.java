package com.moneydance.modules.features.yahooqt;

public abstract class StockUtil {
  
  public static final String replaceAll(String str, String toReplace, String replaceWith) {
    int i;
    int lastI = 0;
    StringBuffer sb = new StringBuffer(str.length());
    while((i=str.indexOf(toReplace, lastI))>=0) {
      sb.append(str.substring(lastI, i)); // add the text before the matched substring
      sb.append(replaceWith);
      lastI = i + toReplace.length();
    }
    sb.append(str.substring(lastI)); // add the rest
    return sb.toString();
  }

  public static boolean areEqual(Object object1, Object object2) {
    if (object1 == object2) return true;                      // either same instance or both null
    if ((object1 == null) || (object2 == null)) return false; // one is null, the other isn't
    return object1.equals(object2);
  }
  
  /**
   * Null safe check for "" (empty string).
   *
   * @param candidate the String to evaluate.
   * @return true if candidate is null or "" (empty string)
   */
  public static boolean isEmpty(String candidate) {
    return candidate == null || candidate.length() == 0;
  }
  
  /**
   * Null safe check for a String with nothing but whitespace characters.
   *
   * @param candidate the String to evaluate.
   * @return true if the candidate is null or all whitespace.
   */
  public static boolean isBlank(String candidate) {
    boolean isBlank = isEmpty(candidate);
    
    if (!isBlank) {
      for (int index = candidate.length()-1; index >= 0; index--) {
        isBlank = Character.isWhitespace(candidate.charAt(index));
        if (!isBlank) {
          break; // non-whitespace character found, don't bother checking the remainder
        }
      }
    }
    return isBlank;
  }
  

}

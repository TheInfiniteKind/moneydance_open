package com.moneydance.modules.features.securityquoteload;

import java.util.List;

public class QLUtil {

  public static boolean isCrypto(String ticker) {
    if (ticker == null) return false;
    return ticker.contains("-");
  }

  public enum ExportFormat {
    HTML, TABDEL, COMMADEL, COMMA_DELIMITED_WITH_BOM, TAB_DELIMITED_WITH_BOM;

    public boolean shouldWriteBOM() {
      return this == COMMA_DELIMITED_WITH_BOM || this == TAB_DELIMITED_WITH_BOM;
    }

    public char getDelimiter() {
      return switch (this) {
        case TABDEL, TAB_DELIMITED_WITH_BOM -> '\t';
        case COMMADEL, COMMA_DELIMITED_WITH_BOM -> ',';
        default -> ' ';
      };
    }

    public String getSaveFilenameExtension() {
      return switch (this) {
        case HTML -> "html";
        case COMMADEL, COMMA_DELIMITED_WITH_BOM -> "csv";
        default -> "txt";
      };
    }
  }

  public static String escapeField(Object value) {
    return escapeField(value, ExportFormat.COMMADEL);
  }

  public static String escapeField(Object value, ExportFormat format) {
    if (value == null) return "";

    String str = value.toString();
    if (str.isBlank()) return str;  // preserve whitespace exactly

    List<Character> detectedChars;
    if (format == ExportFormat.COMMADEL || format == ExportFormat.COMMA_DELIMITED_WITH_BOM) {
      detectedChars = CSV_DELIM_DETECT_CHARS.stream()
                                            .filter(ch -> str.indexOf(ch) >= 0)
                                            .toList();
      if (detectedChars.isEmpty()) return str;
    } else {
      detectedChars = TAB_DELIM_DETECT_CHARS.stream()
                                            .filter(ch -> str.indexOf(ch) >= 0)
                                            .toList();
      if (detectedChars.isEmpty()) return str;
    }

    StringBuilder sb = new StringBuilder();
    sb.append(CHAR_DOUBLE_QUOTE);  // start quote

    if (detectedChars.contains(CHAR_DOUBLE_QUOTE)) {
      for (char c : str.toCharArray()) {
        if (c == CHAR_DOUBLE_QUOTE) {
          sb.append(ESCAPED_QUOTES);  // escape quote
        } else {
          sb.append(c);
        }
      }
    } else {
      sb.append(str);  // no quote escaping needed
    }

    sb.append("\"");  // end quote
    return sb.toString();
  }

  public static final byte[] UTF8_BOM = new byte[]{(byte) 0xEF, (byte) 0xBB, (byte) 0xBF};
  public static final char CHAR_DOUBLE_QUOTE = '"';
  public static final char CHAR_NEWLINE = '\n';
  public static final char CHAR_RETURN = '\r';
  public static final char CHAR_COMMA = ',';
  public static final char CHAR_TAB = '\t';
  public static final String ESCAPED_QUOTES = "\"\"";
  public static final List<Character> CSV_DELIM_DETECT_CHARS = List.of(CHAR_NEWLINE, CHAR_RETURN, CHAR_DOUBLE_QUOTE, CHAR_COMMA);
  public static final List<Character> TAB_DELIM_DETECT_CHARS = List.of(CHAR_NEWLINE, CHAR_RETURN, CHAR_DOUBLE_QUOTE, CHAR_TAB);

}
